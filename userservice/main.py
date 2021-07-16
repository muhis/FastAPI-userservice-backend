import uvicorn
import logging


LOGGER = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    LOGGER.info('### Starting user service ###')
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)