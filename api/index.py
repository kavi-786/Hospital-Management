from app import app

# Vercel expects this
def handler(event, context):
    return app
