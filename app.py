from flask import Flask, render_template, request, redirect, url_for, current_app
import cv2
import numpy as np
from PIL import Image
import io
import base64
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Secure cookie settings recommended for production
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)


def detect_shapes_image_bytes(image_bytes):
    # Read image bytes into OpenCV (BGR)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    np_img = np.array(image)[:, :, ::-1].copy()  # RGB to BGR

    orig = np_img.copy()
    gray = cv2.cvtColor(np_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            continue

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        vertices = len(approx)

        shape_name = "unidentified"
        if vertices == 3:
            shape_name = "triangle"
        elif vertices == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            shape_name = "square" if 0.95 <= ar <= 1.05 else "rectangle"
        elif vertices == 5:
            shape_name = "pentagon"
        elif vertices > 5:
            shape_name = "circle"

        cv2.drawContours(orig, [approx], -1, (0, 255, 0), 2)
        M = cv2.moments(approx)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            (x, y, w, h) = cv2.boundingRect(approx)
            cX, cY = x + w // 2, y + h // 2
        cv2.putText(orig, shape_name, (cX - 40, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    _, buf = cv2.imencode('.png', orig)
    return buf.tobytes()


@app.route('/', methods=['GET', 'POST'])
def index():
    result_url = None
    error = None
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        try:
            image_bytes = file.read()
            processed = detect_shapes_image_bytes(image_bytes)

            # ensure results dir exists under static
            results_dir = os.path.join(app.static_folder or 'static', 'results')
            os.makedirs(results_dir, exist_ok=True)

            # create unique filename
            fname = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.png"
            out_path = os.path.join(results_dir, fname)
            with open(out_path, 'wb') as f:
                f.write(processed)

            result_url = url_for('static', filename=f"results/{fname}")
        except Exception as e:
            current_app.logger.exception('Failed to process image')
            error = str(e)
    return render_template('index.html', result_url=result_url, error=error)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
