from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Lista para almacenar datos (en producción usar base de datos)
temperature_data = []

@app.route('/')
def index():
    """Página principal - Visualización de temperatura en tiempo real"""
    return render_template('index.html')

@app.route('/api/temperature', methods=['POST'])
def receive_temperature():
    """Recibe datos de temperatura del ESP32"""
    try:
        data = request.get_json()
        
        # データ検証
        if not data or 'temperature' not in data:
            return jsonify({'error': 'Invalid data format'}), 400
        
        # タイムスタンプ処理
        if 'timestamp' in data:
            timestamp = data['timestamp']
        else:
            timestamp = datetime.now().isoformat()
        
        # データを保存
        temp_record = {
            'temperature': float(data['temperature']),
            'timestamp': timestamp,
            'device_id': data.get('device_id', 'unknown'),
            'stored_data': data.get('stored_data', False),
            'received_at': datetime.now().isoformat()
        }
        
        temperature_data.append(temp_record)
        
        # 最新1000件のみ保持
        if len(temperature_data) > 1000:
            temperature_data.pop(0)
        
        print(f"温度データ受信: {temp_record['temperature']}°C from {temp_record['device_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Temperature data received',
            'data_count': len(temperature_data)
        }), 200
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature', methods=['GET'])
def get_temperatures():
    """保存された温度データを取得"""
    try:
        # クエリパラメータで件数制限
        limit = request.args.get('limit', 100, type=int)
        
        # 最新のデータから指定件数を取得
        recent_data = temperature_data[-limit:] if temperature_data else []
        
        return jsonify({
            'success': True,
            'data': recent_data,
            'total_count': len(temperature_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature/latest', methods=['GET'])
def get_latest_temperature():
    """最新の温度データを取得"""
    try:
        if not temperature_data:
            return jsonify({
                'success': False,
                'message': 'No data available'
            }), 404
        
        latest = temperature_data[-1]
        return jsonify({
            'success': True,
            'data': latest
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """ヘルスチェック用エンドポイント"""
    return jsonify({
        'status': 'healthy',
        'data_count': len(temperature_data),
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)