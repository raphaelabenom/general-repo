from minio_client import MinioClient
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Configurações do MinIO
    endpoint = os.getenv("ENDPOINT_KEY")
    access_key = os.getenv("ACESS_KEY")
    secret_key = os.getenv("SECRET_KEY")

    client = MinioClient(endpoint, access_key, secret_key)

    # Exemplos de uso
    client.create_bucket("test-bucket")
    client.upload_file("test-bucket", "/path/to/file.txt", "file.txt")
    client.upload_folder("test-bucket", "/path/")
    client.read_bucket("test-bucket")
    client.update_bucket("test-bucket", "new-test-bucket")
    client.delete_bucket("new-test-bucket")
