# create_corpus_and_upload_data.py
from __future__ import annotations

import os
import tempfile
from typing import Optional

from dotenv import load_dotenv
from google.auth import default as google_auth_default
from google.api_core.exceptions import ResourceExhausted, Forbidden, NotFound
from google.cloud import storage
import vertexai
from vertexai.preview import rag


# ---------- Configuration (editable) ----------
# Display name & description for the RAG corpus
CORPUS_DISPLAY_NAME = "Cymbal_Pets_Documentation"
CORPUS_DESCRIPTION = "Corpus containing documentation about care for pets (dogs, cats, ...)"

# GCS source info (bucket + object). You can also set these via .env if you prefer.

# Path to your project's .env, relative to this file. Adjust if your structure differs.
ENV_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".env")
)

DEFAULT_FILE_DESCRIPTION = "Imported from Google Cloud Storage into Vertex AI RAG Engine."


class DocRAGIngestor:
    """
    End-to-end helper to:
      1) Initialize Vertex AI with ADC credentials.
      2) Create or retrieve a RAG corpus configured with the embedding model.
      3) Download one or more files from GCS to local temp files.
      4) Upload the file(s) into the RAG corpus.
      5) Print the corpus name for downstream use.
      6) List files currently in the corpus (sanity check).
    """

    def __init__(self, project_id: str, location: str):
        """
        Args:
            project_id: GCP project ID (e.g., "my-project-123").
            location: Vertex AI location/region (e.g., "us-central1", "europe-west1").
        """
        self.project_id = project_id
        self.location = location
        self.credentials = None
        self.corpus = None  # Will hold the rag.Corpus once created/retrieved

    def initialize_vertex_ai_client(self) -> None:
        """
        Initializes Vertex AI SDK with Application Default Credentials (ADC).
        Raises if credentials cannot be found.
        """
        self.credentials, _ = google_auth_default()
        vertexai.init(
            project=self.project_id,
            location=self.location,
            credentials=self.credentials,
        )
        print(f"✔ Vertex AI initialized for project '{self.project_id}' in '{self.location}'")

    def get_or_create_rag_corpus(self) -> rag.Corpus:
        """
        Gets an existing RAG corpus by display name or creates a new one using
        the specified embedding model.
        """
        embedding_model_config = rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-004"
        )

        print(f"ℹ Searching for an existing corpus named '{CORPUS_DISPLAY_NAME}'...")
        for existing in rag.list_corpora():
            if existing.display_name == CORPUS_DISPLAY_NAME:
                self.corpus = existing
                print(f"✔ Found existing corpus: display_name='{existing.display_name}', name='{existing.name}'")
                return existing

        print("⚠ No existing corpus found; creating a new one...")
        self.corpus = rag.create_corpus(
            display_name=CORPUS_DISPLAY_NAME,
            description=CORPUS_DESCRIPTION,
            embedding_model_config=embedding_model_config,
        )
        print(f"✔ Created corpus: display_name='{self.corpus.display_name}', name='{self.corpus.name}'")
        return self.corpus

    def _parse_gcs_uri(self, gcs_uri: str) -> tuple[str, str]:
        """
        Parses a GCS URI into (bucket_name, blob_name_or_prefix).
        """
        if not gcs_uri.startswith("gs://"):
            raise ValueError("GCS URI must start with 'gs://'")
        path = gcs_uri[5:]  # strip gs://
        parts = path.split("/", 1)
        if not parts[0]:
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")
        blob_name = parts[1] if len(parts) == 2 else ""
        return parts[0], blob_name

    def _storage_client(self) -> storage.Client:
        """
        Creates a Storage client using the initialized ADC credentials.
        """
        return storage.Client(credentials=self.credentials, project=self.project_id)

    def _list_blobs_for_prefix(
        self, client: storage.Client, bucket_name: str, prefix: str
    ) -> list[storage.Blob]:
        """
        Lists real objects under a GCS prefix, skipping pseudo-folder placeholders.
        """
        blobs = [
            blob
            for blob in client.list_blobs(bucket_name, prefix=prefix)
            if blob.name and not blob.name.endswith("/")
        ]
        return sorted(blobs, key=lambda blob: blob.name)

    def list_gcs_files(self, gcs_uri: str) -> list[storage.Blob]:
        """
        Resolves a GCS URI into one or more downloadable blobs.

        The URI may point to:
          - a single object, e.g. gs://my-bucket/path/file.pdf
          - a prefix/folder, e.g. gs://my-bucket/path/
          - a prefix without trailing slash, e.g. gs://my-bucket/path
          - a whole bucket, e.g. gs://my-bucket
        """
        bucket_name, blob_name = self._parse_gcs_uri(gcs_uri)
        client = self._storage_client()

        try:
            bucket = client.bucket(bucket_name)

            if not blob_name or blob_name.endswith("/"):
                blobs = self._list_blobs_for_prefix(client, bucket_name, blob_name)
            else:
                exact_blob = bucket.blob(blob_name)
                if exact_blob.exists(client):
                    blobs = [exact_blob]
                else:
                    prefix = f"{blob_name.rstrip('/')}/"
                    blobs = self._list_blobs_for_prefix(client, bucket_name, prefix)

            if not blobs:
                raise NotFound(f"No files found for GCS URI: {gcs_uri}")

            print(f"✔ Found {len(blobs)} GCS file(s) to ingest from '{gcs_uri}'.")
            return blobs
        except Forbidden as e:
            print("⛔ Forbidden: Check IAM permissions for the service account/ADC.")
            print("   Required roles usually include 'Storage Object Viewer' on the bucket.")
            raise e
        except NotFound as e:
            print("❓ Not found: Verify bucket/object or prefix name and region.")
            raise e

    def download_gcs_blob(self, blob: storage.Blob, local_path: str) -> str:
        """
        Downloads a GCS blob to a local path.
        """
        gcs_uri = f"gs://{blob.bucket.name}/{blob.name}"
        print(f"⬇ Downloading from GCS: '{gcs_uri}' -> '{local_path}'")

        try:
            blob.download_to_filename(local_path)
        except Forbidden as e:
            print("⛔ Forbidden: Check IAM permissions for the service account/ADC.")
            print("   Required roles usually include 'Storage Object Viewer' on the bucket.")
            raise e
        except NotFound as e:
            print("❓ Not found: Verify bucket/object name and region.")
            raise e

        print("✔ GCS download complete.")
        return local_path

    def download_gcs_file(self, gcs_uri: str, local_path: str) -> str:
        """
        Downloads a single file from GCS to a local path using google-cloud-storage.

        Args:
            gcs_uri: Full GCS URI (e.g., gs://my-bucket/path/to/file.pdf)
            local_path: Local file path to write to.

        Returns:
            The local path of the downloaded file.

        Raises:
            google.api_core.exceptions.Forbidden: if permissions are insufficient.
            google.api_core.exceptions.NotFound: if bucket/blob doesn't exist.
        """
        bucket_name, blob_name = self._parse_gcs_uri(gcs_uri)
        if not blob_name:
            raise ValueError("GCS URI must include an object name for single-file download.")

        client = self._storage_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return self.download_gcs_blob(blob, local_path)

    def upload_file_into_corpus(self, local_path: str, display_name: str, description: str) -> Optional[rag.File]:
        """
        Uploads a local file into the current corpus.

        Args:
            local_path: local file path to upload.
            display_name: human-readable name shown in RAG console.
            description: short description for the file.

        Returns:
            The created rag.File, or None if upload failed due to quota or other errors.
        """
        if not self.corpus:
            raise RuntimeError("Corpus not initialized. Call get_or_create_rag_corpus() first.")

        print(f"⬆ Uploading '{display_name}' into corpus '{self.corpus.display_name}'...")
        try:
            rag_file = rag.upload_file(
                corpus_name=self.corpus.name,
                path=local_path,
                display_name=display_name,
                description=description,
            )
            print(f"✔ Upload successful: file_name='{rag_file.name}'")
            return rag_file
        except ResourceExhausted as e:
            print(f"Quota exceeded while uploading '{display_name}': {e}")
            print("   Tip: Request a higher quota for text-embedding-004 in Cloud Console.")
            return None
        except Exception as e:
            print(f"⚠ Unexpected error uploading '{display_name}': {e}")
            return None

    def print_corpus_env_value(self) -> None:
        """
        Prints RAG_CORPUS without modifying the local .env file.
        """
        if not self.corpus:
            raise RuntimeError("Corpus not initialized. Cannot print RAG_CORPUS.")
        print("Set this in your .env if needed:")
        print(f"RAG_CORPUS={self.corpus.name}")

    def print_corpus_file_inventory(self) -> None:
        """
        Lists files currently in the corpus (for sanity checking).
        """
        if not self.corpus:
            raise RuntimeError("Corpus not initialized. Call get_or_create_rag_corpus() first.")

        files = list(rag.list_files(corpus_name=self.corpus.name))
        print(f"📦 Files in corpus '{self.corpus.display_name}' ({len(files)} total):")
        for f in files:
            print(f"  • {f.display_name}  —  {f.name}")


def main():
    # --- Load environment variables from .env and validate required config ---
    load_dotenv(ENV_FILE_PATH)

    project_id = _require_env("GOOGLE_CLOUD_PROJECT")
    location = _require_env("GOOGLE_CLOUD_LOCATION")
    gcs_uri = _require_env("GCS_URI")
    local_temp_filename = os.getenv("LOCAL_TEMP_FILENAME")

    # --- Instantiate the ingestor and run the sequence ---
    ingestor = DocRAGIngestor(project_id=project_id, location=location)

    ingestor.initialize_vertex_ai_client()
    ingestor.get_or_create_rag_corpus()
    ingestor.print_corpus_env_value()

    # Use a temporary directory for clean local storage
    with tempfile.TemporaryDirectory() as tmpdir:
        gcs_files = ingestor.list_gcs_files(gcs_uri)
        total_files = len(gcs_files)

        for index, blob in enumerate(gcs_files, start=1):
            local_filename = _local_filename_for_blob(
                blob_name=blob.name,
                index=index,
                total_files=total_files,
                local_temp_filename=local_temp_filename,
            )
            display_name = _display_name_for_blob(
                blob_name=blob.name,
                total_files=total_files,
                local_temp_filename=local_temp_filename,
            )
            local_path = os.path.join(tmpdir, local_filename)

            # 1) Download the file from GCS
            ingestor.download_gcs_blob(blob, local_path)

            # 2) Upload the file into the corpus
            ingestor.upload_file_into_corpus(
                local_path=local_path,
                display_name=display_name,
                description=(
                    f"{DEFAULT_FILE_DESCRIPTION} "
                    f"Source: gs://{blob.bucket.name}/{blob.name}"
                ),
            )

    # 3) Show a corpus inventory for verification
    ingestor.print_corpus_file_inventory()


def _require_env(name: str) -> str:
    """
    Reads a required environment variable and fails with a clear message if absent.
    """
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} not set in .env")
    return value


def _display_name_for_blob(
    blob_name: str, total_files: int, local_temp_filename: Optional[str]
) -> str:
    """
    Uses the legacy LOCAL_TEMP_FILENAME display name for single-file ingestion.
    """
    if total_files == 1 and local_temp_filename:
        return local_temp_filename
    return os.path.basename(blob_name.rstrip("/")) or blob_name


def _local_filename_for_blob(
    blob_name: str,
    index: int,
    total_files: int,
    local_temp_filename: Optional[str],
) -> str:
    """
    Builds a temporary local filename for one blob.
    """
    if total_files == 1 and local_temp_filename:
        return local_temp_filename

    filename = os.path.basename(blob_name.rstrip("/")) or f"gcs_file_{index}"
    if total_files == 1:
        return filename
    return f"{index:04d}_{filename}"


if __name__ == "__main__":
    main()
