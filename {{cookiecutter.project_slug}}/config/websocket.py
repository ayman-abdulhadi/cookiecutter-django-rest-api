import json

async def websocket_application(scope, receive, send):
    """
    Simple websocket echo server for API notifications.
    This is a basic implementation that can be expanded for real-time API updates.
    """
    while True:
        event = await receive()

        if event["type"] == "websocket.connect":
            await send({"type": "websocket.accept"})

        if event["type"] == "websocket.disconnect":
            break

        if event["type"] == "websocket.receive":
            # Echo the received message with a JSON wrapper
            if "text" in event:
                response_data = {
                    "message": event["text"],
                    "status": "received"
                }
                await send({
                    "type": "websocket.send",
                    "text": json.dumps(response_data)
                })
            elif "bytes" in event:
                await send({
                    "type": "websocket.send",
                    "bytes": event["bytes"]
                })
