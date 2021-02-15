from datetime import datetime
from flask import Flask, session, jsonify, request


class AppointmentCollision(Exception):
	def __init__(self):
		Exception.__init__(self)
		self.message = "Error: An appointment for that user has already been made for that date"
		self.status_code = 400

	def to_dict(self):
		rv = {"message": self.message}
		return rv


app = Flask(__name__)
app.secret_key = "secret key"


@app.route("/get_appt", methods=['GET'])
def get_appt():
	email = request.args.get("email")
	if email in session:
		appointments = [dt.strftime("%Y-%m-%d %H:%M") for dt in session[email]]
		return {"payload": appointments}
	else:
		return {"payload": "No appointments found for {}".format(email)}


@app.route("/set_appt", methods=["POST"])
def set_appt():
	email = request.json["email"]
	dt_string = request.json["date"] + " " + request.json["time"]
	appt_time = datetime.strptime(dt_string,"%Y-%m-%d %H:%M")
	if email in session:
		same_dates = [day for day in session[email] if day.date() == appt_time.date()]
		if same_dates:
			raise AppointmentCollision()
		else:
			appt_list = session.get(email)
			appt_list.append(appt_time)
			session[email] = appt_list
	else:
		session[email] = [appt_time]
	return {"payload": "An appointment for {} was made at {}".format(email, appt_time,session.keys())}


@app.errorhandler(AppointmentCollision)
def handle_appointment_collision(error):
	response = jsonify(error.to_dict())
	response.status_code = error.status_code
	return response


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

