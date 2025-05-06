import uuid
from flask import Flask, request, jsonify
from utils import get_chroma_client, chunk_text, embed_chunks, read_document_content, compute_file_hash

app = Flask(__name__)

chroma_client = get_chroma_client()
@app.route('/api/documents/process', methods=['POST'])
def process_document():
    if 'file' not in request.files or request.files["file"].filename == "":
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        content, raw_bytes = read_document_content(file)
        file_hash = compute_file_hash(raw_bytes)

        # Check for existing file in ChromaDB
        collection = chroma_client.get_collection(name='documents')
        existing = collection.get(where={"file_hash": file_hash}, limit=1)
        if existing['metadatas']:
            asset_id = existing['metadatas'][0].get('asset_id')
            return jsonify({'message': 'File already uploaded', 'asset_id': asset_id}), 200

    except Exception as e:
        return jsonify({'error': f'File processing failed: {e}'}), 500

    chunks = chunk_text(content)
    if not chunks:
        return jsonify({'error': 'No content to process'}), 400

    asset_id = str(uuid.uuid4())
    embed_chunks(chroma_client, chunks, file_hash, asset_id)


    return jsonify({'asset_id': asset_id}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
