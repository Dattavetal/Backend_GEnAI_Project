import uuid
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from utils import get_chroma_client, retrieve_relevant_chunks, stream_chat_llm7

app = Flask(__name__)
CORS(app)

# Initialize ChromaDB client
chroma_client = get_chroma_client()
chat_threads = {}

@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    try:
        data = request.get_json() or {}
        asset_id = data.get('asset_id')
        if not asset_id:
            return jsonify({'error':'Missing asset_id'}),400

        thread_id = uuid.uuid4().hex
        chat_threads[thread_id] = {"asset_id":asset_id, "history":[]}
        return jsonify({'thread_id':thread_id}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    try:
        data = request.get_json() or {}
        thread_id = data.get('thread_id')
        user_msg  = data.get('message')
        if not thread_id or not user_msg:
            return jsonify({'error':'Missing thread_id or message'}),400
        if thread_id not in chat_threads:
            return jsonify({'error':'Invalid thread_id'}),404

        # Append to history
        chat_threads[thread_id]['history'].append({'role':'user','content':user_msg})

        def event_stream():
            try:
                # 1) Retrieve context
                chunks = retrieve_relevant_chunks(
                    chroma_client,
                    chat_threads[thread_id]['asset_id'],
                    user_msg,
                    app.config['TOP_K']
                )
                

                # 2) Stream tokens
                bot_response = ""
                prev_token=""
                for token in stream_chat_llm7(user_msg, chunks):
                    bot_response += token
                    yield f"data: {token}\n\n"

            except Exception as e:
                # Catch-all
                yield f"event:error\ndata:{e}\n\n"
            finally:
                # Finalize history
                chat_threads[thread_id]['history'].append({'role':'assistant','content':bot_response})
                yield "event:done\ndata:\n\n"

        return Response(event_stream(), mimetype='text/event-stream')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/api/chat/history', methods=['GET'])
def chat_history():
    tid = request.args.get('thread_id')
    if not tid or tid not in chat_threads:
        return jsonify({'error':'Invalid thread_id'}),404
    return jsonify({'history':chat_threads[tid]['history']}),200

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5002,debug=True)
