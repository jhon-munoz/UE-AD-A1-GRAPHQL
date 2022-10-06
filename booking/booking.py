import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc
import json
from google.protobuf.json_format import MessageToJson

EMPTY_BOOKING_DATA = booking_pb2.BookingData(userid="", dates="")


class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def GetListBookings(self, request, context):
        for booking in self.db:
            yield booking_pb2.BookingData(userid=booking['userid'],
                                          dates=booking['dates'])

    def GetBookingByUserId(self, request, context):
        for booking in self.db:
            if booking['userid'] == request.userid:
                return booking_pb2.BookingFeedback(
                    message='Booking found!',
                    booking=booking_pb2.BookingData(**booking))
        return booking_pb2.BookingFeedback(message='Booking not found!',
                                           booking=EMPTY_BOOKING_DATA)

    def AddBookingByUserId(self, request, context):
        date = request.date
        movieid = request.movieid
        userid = request.userid

        # check if movie is available at this date
        with grpc.insecure_channel('localhost:3002') as channel:
            stub = showtime_pb2_grpc.ShowtimeStub(channel)
            movies = list(
                map(lambda x: x.movieid,
                    stub.GetMoviesByDate(showtime_pb2.Date(date=date))))

        if movieid not in movies:
            return booking_pb2.BookingFeedback(
                message='movie not available at this date',
                booking=EMPTY_BOOKING_DATA)

        for booking in self.db:

            # there are already movies for this user
            if booking['userid'] == userid:
                date_objs = booking['dates']
                for date_obj in date_objs:

                    # there are already movies in this date
                    if date_obj['date'] == date:

                        # movie already in this date for this user
                        if movieid in date_obj['movies']:
                            return booking_pb2.BookingFeedback(
                                message=
                                'an existing item already exists with this id',
                                booking=EMPTY_BOOKING_DATA)

                        # add movie to this date
                        date_obj['movies'].append(movieid)
                        return booking_pb2.BookingFeedback(
                            message='booking added',
                            booking=booking_pb2.BookingData(**booking))

                # add new date to user
                date_objs.append({
                    'date': date,
                    'movies': [movieid],
                })
                return booking_pb2.BookingFeedback(
                    message='booking added',
                    booking=booking_pb2.BookingData(**booking))

        # add new user
        booking = {
            'userid': userid,
            'dates': [{
                'date': date,
                'movies': [movieid],
            }],
        }
        self.db.append(booking)
        return booking_pb2.BookingFeedback(
            message='booking added', booking=booking_pb2.BookingData(**booking))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
