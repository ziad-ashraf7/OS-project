import os
from flask import send_from_directory
from flask import Flask, render_template, request, jsonify
from process import Process
from scheduling_algorithms import SchedulingAlgorithms
import random
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_processes', methods=['POST'])
def generate_processes():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.get_json()
        if not data or 'num_processes' not in data:
            return jsonify({'error': 'Missing num_processes in request'}), 400

        try:
            num_processes = int(data['num_processes'])
        except (ValueError, TypeError):
            return jsonify({'error': 'num_processes must be a valid integer'}), 400

        if num_processes <= 0:
            return jsonify({'error': 'Number of processes must be positive'}), 400

        processes = Process.generate_random_processes(num_processes)
        processes_data = [{
            'pid': p.pid,
            'arrival_time': p.arrival_time,
            'burst_time': p.burst_time,
            'priority': p.priority
        } for p in processes]

        return jsonify({'processes': processes_data})

    except Exception as e:
        app.logger.error(f"Error generating processes: {str(e)}")
        return jsonify({'error': 'Internal server error while generating processes'}), 500

@app.route('/run_algorithm', methods=['POST'])
def run_algorithm():
    data = request.json
    algorithm = data['algorithm']
    processes_data = data['processes']
    time_quantum = data.get('time_quantum', 2)

    # Convert JSON data to Process objects
    processes = []
    for p in processes_data:
        process = Process(
            pid=p['pid'],
            arrival_time=p['arrival_time'],
            burst_time=p['burst_time'],
            priority=p['priority']
        )
        processes.append(process)

    # Reset process states
    for process in processes:
        process.remaining_time = process.burst_time
        process.start_time = None
        process.completion_time = None
        process.waiting_time = 0
        process.turnaround_time = 0
        process.response_time = None

    try:
        # Run selected algorithm
        if algorithm == "FCFS":
            result_processes, gantt_chart = SchedulingAlgorithms.fcfs(processes)
        elif algorithm == "SJF":
            result_processes, gantt_chart = SchedulingAlgorithms.srtf(processes)  # Changed to SRTF (preemptive)
        elif algorithm == "Priority":
            result_processes, gantt_chart = SchedulingAlgorithms.priority(processes)
        elif algorithm == "RR":
            try:
                time_quantum = int(time_quantum)
                if time_quantum <= 0:
                    return jsonify({'error': 'Time quantum must be positive'}), 400
                result_processes, gantt_chart = SchedulingAlgorithms.round_robin(processes, time_quantum)
            except ValueError:
                return jsonify({'error': 'Please enter a valid time quantum'}), 400

        # Prepare response data
        metrics = []
        total_waiting = 0
        total_turnaround = 0
        total_response = 0
        count = len(result_processes)

        for process in result_processes:
            metrics.append({
                'pid': process.pid,
                'waiting_time': process.waiting_time,
                'turnaround_time': process.turnaround_time,
                'response_time': process.response_time if process.response_time is not None else None
            })
            total_waiting += process.waiting_time
            total_turnaround += process.turnaround_time
            if process.response_time is not None:
                total_response += process.response_time

        avg_waiting = total_waiting / count
        avg_turnaround = total_turnaround / count
        avg_response = total_response / count if total_response > 0 else 0

        return jsonify({
            'algorithm': algorithm,
            'metrics': metrics,
            'gantt_chart': gantt_chart,
            'averages': {
                'waiting_time': avg_waiting,
                'turnaround_time': avg_turnaround,
                'response_time': avg_response
            }
        })
    except Exception as e:
        return jsonify({'error': f'Failed to run {algorithm} algorithm: {str(e)}'}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.txt')
        file.save(input_path)

        try:
            processes = Process.generate_processes_from_file(input_path)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.txt')
            Process.write_to_file(processes, output_path)

            processes_data = [{
                'pid': p.pid,
                'arrival_time': p.arrival_time,
                'burst_time': p.burst_time,
                'priority': p.priority
            } for p in processes]

            return jsonify({
                'message': 'File processed successfully',
                'processes': processes_data,
                'download_url': '/download/output.txt'
            })
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
'''adsfdsff'''
if __name__ == '__main__':
    app.run(debug=True, port=6000)