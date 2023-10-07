class QueueContent():
    def __init__(self, client_id, question_num=None, time_estimate=None, question_notes=None):
        self.client_id = client_id
        self.question_num = question_num
        self.question_notes = question_notes
        self.time_estimate = time_estimate


    def __repr__(self):
        return f' Client name: {self.client_id} \n question_number: {self.question_num} \n time estimate: {self.time_estimate} \n notes: {self.question_notes} \n'
