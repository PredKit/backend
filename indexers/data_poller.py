"""
Data Poller - Cloud Function for polling external data sources
"""
import functions_framework
from google.cloud import pubsub_v1
import httpx
import json
from shared.database import get_db_connection
from shared.utils import logger


@functions_framework.cloud_event
def poll_data(cloud_event):
    """Cloud Function triggered by Pub/Sub for data polling"""
    
    try:
        logger.info("Starting data polling job")
        
        # Poll external APIs or data sources
        data = poll_external_sources()
        
        # Store in database
        if data:
            store_data(data)
            logger.info(f"Stored {len(data)} records")
        
        # Trigger indexing if needed
        trigger_indexing()
        
    except Exception as e:
        logger.error(f"Data polling error: {str(e)}")
        raise


def poll_external_sources():
    """Poll external data sources"""
    data = []
    
    # Example: Poll an API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            if response.status_code == 200:
                data.extend(response.json())
    except Exception as e:
        logger.error(f"Failed to poll external source: {str(e)}")
    
    return data


def store_data(data):
    """Store data in database"""
    conn = get_db_connection()
    # Implementation depends on your data structure
    pass


def trigger_indexing():
    """Trigger indexing function via Pub/Sub"""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path("your-project-id", "indexing-topic")
    
    message = json.dumps({"action": "index_new_data"}).encode("utf-8")
    publisher.publish(topic_path, message)
    logger.info("Triggered indexing job")
