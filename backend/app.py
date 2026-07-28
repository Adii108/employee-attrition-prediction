import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.config import API_TITLE, API_DESCRIPTION, API_VERSION, ALLOWED_HOSTS
from backend.routes.prediction import router as prediction_router

# Initialize FastAPI App
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handler for Pydantic Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats validation errors into a clean, human-readable dictionary."""
    errors = {}
    for error in exc.errors():
        # Get the field name (usually the last element of the loc tuple)
        field = str(error.get("loc", [-1])[-1])
        msg = error.get("msg", "Invalid input value.")
        
        # Make the messages slightly friendlier if possible
        if "type_error" in error.get("type", ""):
            msg = f"Invalid data type. {msg}"
            
        errors[field] = msg

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "One or more input fields failed validation checks.",
            "details": errors
        }
    )

# Register Prediction Router
app.include_router(prediction_router)

if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
