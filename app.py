import os
import boto3
from flask import Flask, jsonify, request

# from aws_xray_sdk.core import xray_recorder
# from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
 
app = Flask(__name__)
 
# xray_recorder.configure(service="course-service")
# XRayMiddleware(app, xray_recorder)
 
REGION = os.environ.get("AWS_REGION", "ap-south-2")
 
dynamodb  	= boto3.resource("dynamodb", region_name=REGION)
courses_table = dynamodb.Table("course-akhil")
 
 
@app.route("/health")
def health():
	return jsonify({"status": "ok", "service": "course-service"}), 200
 
 
@app.route("/courses/<course_code>", methods=["GET"])
def get_course(course_code):
	resp = courses_table.get_item(Key={"id": course_code})
	item = resp.get("Item")
	if not item:
		return jsonify({"error": "Course not found"}), 404
	return jsonify(item), 200
 
 
@app.route("/courses", methods=["GET"])
def list_courses():
	resp = courses_table.scan(Limit=50)
	return jsonify(resp.get("Items", [])), 200

@app.route("/courses", methods=["POST"])
def add_course():
    try:
        data = request.get_json(force=True)

        # Validate required fields
        if "id" not in data or "course" not in data:
            return jsonify({"error": "Missing required fields: id, title"}), 400

        # Put item into DynamoDB
        courses_table.put_item(Item={
            "id": data["id"],          # Partition key
            "course": data["course"]
        })

        return jsonify({"message": "Course added successfully", "course": data}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=False)
