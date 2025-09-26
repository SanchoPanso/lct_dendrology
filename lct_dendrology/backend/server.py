"""FastAPI server for image processing inference."""

from typing import Dict, Any
import logging

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from lct_dendrology.cfg import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="LCT Dendrology API",
    description="API для обработки изображений в дендрологических исследованиях",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "LCT Dendrology API is running"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/process-image")
async def process_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Обрабатывает загруженное изображение и возвращает результат анализа.
    
    Args:
        file: Загруженный файл изображения
        
    Returns:
        Dict с результатами анализа изображения
        
    Raises:
        HTTPException: Если файл не является изображением или произошла ошибка
    """
    # Проверяем, что файл является изображением
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail="Файл должен быть изображением"
        )
    
    try:
        # Читаем содержимое файла
        content = await file.read()
        
        logger.info(f"Получено изображение: {file.filename}, размер: {len(content)} байт")
        
        # TODO: Здесь будет реальная обработка изображения с помощью нейросети
        # На данный момент возвращаем заглушку
        result = {
            "filename": file.filename,
            "file_size": len(content),
            "content_type": file.content_type,
            "analysis_result": {}  # Заглушка - пустой словарь
        }
        
        logger.info(f"Обработка завершена для файла: {file.filename}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке изображения: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
