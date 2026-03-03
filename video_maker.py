from flask import Flask, render_template, request, send_file
from moviepy import ImageClip, concatenate_videoclips, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Limit upload size (50MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024


@app.route('/')
def home():
    return render_template('photo_home.html')


@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist("photos")
    duration = int(request.form.get("duration", 3))

    if not files:
        return "No files uploaded"

    image_paths = []

    for file in files:
        unique_name = str(uuid.uuid4()) + "_" + file.filename
        filepath = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(filepath)
        image_paths.append(filepath)

    clips = []

    # LOWER resolution to prevent Railway crash
    TARGET_WIDTH = 854
    TARGET_HEIGHT = 480

    for img in image_paths:
        clip = ImageClip(img)
        clip = clip.resized(height=TARGET_HEIGHT)

        background = ColorClip(
            size=(TARGET_WIDTH, TARGET_HEIGHT),
            color=(0, 0, 0)
        ).with_duration(duration)

        clip = clip.with_position("center").with_duration(duration)

        final_clip = CompositeVideoClip([background, clip])
        clips.append(final_clip)

    final_video = concatenate_videoclips(clips)

    output_filename = str(uuid.uuid4()) + "_final_video.mp4"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264"
    )

    # Clean uploaded images
    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)

    return send_file(output_path, as_attachment=True)


# Railway production port handling
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
