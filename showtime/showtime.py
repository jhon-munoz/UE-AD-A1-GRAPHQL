import grpc
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import json


class ShowtimeServicer(showtime_pb2_grpc.ShowtimeServicer):

    def __init__(self):
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]

    def GetMoviesByDate(self, request, context):
        print('Request received for GetMoviesByDate')
        print(f'Request message:\n{request}')

        for time in self.db:
            if time['date'] == request.date:
                print("Schedule found!")
                for movieid in time['movies']:
                    print(f'Yielding movieid {movieid}')
                    yield showtime_pb2.ShowtimeMovieId(movieid=movieid)

    def GetListTimes(self, request, context):
        print('Request received for GetListTimes')
        print(f'Request message:\n{request}')

        for time in self.db:
            print(f'Yielding schedule {time}')
            yield showtime_pb2.TimesData(date=time['date'],
                                         movies=time['movies'])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowtimeServicer_to_server(ShowtimeServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
