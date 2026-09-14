"""AWS Lambda entrypoint — serves the FastAPI app behind a Function URL."""

from mangum import Mangum

from candlefree.api.main import app

handler = Mangum(app)
