from app import app

if __name__ == '__main__':
    print(app.config['DEBUG'])
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
