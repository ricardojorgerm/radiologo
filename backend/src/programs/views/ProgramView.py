import rest_framework.status as status
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from radiologo.permissions import IsProgrammingR, IsDirector, IsRadiologoDeveloper, IsTechnicalLogisticR, \
    IsCommunicationMarketingR, IsAdministration, IsProgramOwnerR
from radiologo.permissions import IsProgrammingRW, IsProgramOwner, IsTechnicalLogisticRW
from .. import tasks
from ..models.program import Program
from ..serializers.ProgramSerializer import ProgramSerializer
from ..services.ProgramService import ProgramService
from ..services.RemoteService import RemoteService
from ..services.SlotService import SlotService
from ..services.processing.ProcessingService import ProcessingService
from ..services.rss_upload.FeedService import FeedService


class ListCreateProgramsView(APIView):
    permission_classes = (
        IsAuthenticated, (
                IsAdministration | IsDirector | IsRadiologoDeveloper |
                IsProgrammingR | IsTechnicalLogisticR | IsCommunicationMarketingR
        )
    )

    def get(self, request):
        programs = [program for program in Program.objects.all().order_by('name')]
        serialized = ProgramSerializer(programs, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serialized = ProgramSerializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        serialized.save()
        return Response(serialized.data, status=status.HTTP_201_CREATED)


class GetUpdateDeleteProgramView(APIView):
    permission_classes = (
        IsAuthenticated, (
                IsAdministration | IsDirector | IsRadiologoDeveloper |
                IsProgrammingR | IsTechnicalLogisticR | IsCommunicationMarketingR |
                IsProgramOwnerR
        )
    )

    def get(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        serialized = ProgramSerializer(program)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        serialized = ProgramSerializer(program, data=request.data, partial=True)
        serialized.is_valid(raise_exception=True)
        serialized.save()
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        program.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UploadProgramView(APIView):
    permission_classes = (
        IsAuthenticated, (
                IsAdministration | IsDirector | IsRadiologoDeveloper |
                IsProgramOwner | IsProgrammingRW | IsTechnicalLogisticRW
        )
    )

    def put(self, request, pk):
        program = Program.objects.get(pk=pk)

        ProcessingService.save_file(uploaded_file=request.data['file'], emission_date=request.data['date'],
                                    program=program)

        tasks.process_audio.delay(uploaded_file_path=settings.FILE_UPLOAD_DIR + request.data['file'].name,
                                  program_pk=program.pk,
                                  uploader=request.user.author_name,
                                  email=request.user.email,
                                  emission_date=request.data['date'])

        return Response(status=status.HTTP_200_OK)


class GetUpdateDeleteRSSView(APIView):
    permission_classes = (
        IsAuthenticated, (
                IsAdministration | IsDirector | IsRadiologoDeveloper |
                IsProgrammingRW | IsTechnicalLogisticRW
        )
    )

    def get(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        rss_feed_url = program.rss_feed_url
        rss_status = program.rss_feed_status
        return Response(status=status.HTTP_200_OK,
                        data={'feed_url': rss_feed_url, 'feed_status': rss_status})

    def patch(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        new_url = request.data['feed_url']
        new_status = request.data['feed_status']
        try:
            _, feed_name = FeedService.list_episodes_in_podcast(new_url)
            assert type(new_status) is bool
        except Exception:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        program.rss_feed_url = new_url
        program.rss_feed_status = new_status
        program.save()
        return Response(status=status.HTTP_201_CREATED,
                        data={ 'feed_name': feed_name,
                        'feed_url': program.rss_feed_url, 
                        'feed_status': program.rss_feed_status})

    def delete(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        program.rss_feed_url = ""
        program.rss_feed_status = False
        program.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetDeleteArchiveProgramView(APIView):
    permission_classes = (
        IsAuthenticated, (
                IsAdministration | IsDirector | IsRadiologoDeveloper |
                IsProgrammingRW | IsTechnicalLogisticRW | IsCommunicationMarketingR |
                IsProgramOwner
        )
    )

    def get(self, request, pk, date):
        program = get_object_or_404(Program, pk=pk)
        return RemoteService().download_archive_file(program, date)

    def delete(self, request, pk, date):
        program = get_object_or_404(Program, pk=pk)
        RemoteService().delete_archive_file(program, date)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetArchiveContentsView(APIView):
    permission_classes = (
        IsAuthenticated, (
                IsAdministration | IsDirector | IsRadiologoDeveloper |
                IsProgrammingR | IsTechnicalLogisticR | IsCommunicationMarketingR |
                IsProgramOwner
        )
    )

    def get(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        file_list = RemoteService().get_archive_contents(program.normalized_name())
        return Response(status=status.HTTP_200_OK, data=file_list)


class GetArchiveStatistics(APIView):
    permission_classes = (
        IsAuthenticated, (
                IsAdministration | IsDirector | IsRadiologoDeveloper |
                IsProgrammingR | IsTechnicalLogisticR | IsCommunicationMarketingR |
                IsProgramOwner
        )
    )

    def get(self, request):
        stats = RemoteService().get_archive_stats()
        return Response(status=status.HTTP_200_OK, data=stats)


class GetProgramAlreadyUploadedDates(APIView):
    permission_classes = UploadProgramView.permission_classes

    def get(self, request, pk):
        program = Program.objects.get(pk=pk)
        dates = RemoteService().get_uploaded_dates(program)
        return Response(status=status.HTTP_200_OK, data=dates)


class GetWeeklySchedule(APIView):
    permission_classes = ()

    def get(self, request):
        schedule = ProgramService().get_schedule()
        return Response(status=status.HTTP_200_OK, data=schedule)


class GetArchiveNextUpload(APIView):
    permission_classes = GetProgramAlreadyUploadedDates.permission_classes

    def get(self, request, pk):
        program = get_object_or_404(Program, pk=pk)
        return Response(status=status.HTTP_200_OK, data=program.next_upload_date())


class GetFreeSlots(APIView):
    permission_classes = GetUpdateDeleteProgramView.permission_classes

    def get(self, request):
        weekdays = request.GET.get('weekdays').split(',')
        if weekdays[0] != '':
            weekdays = [int(x) for x in weekdays]
        duration = int(request.GET.get('duration'))
        pk = int(request.GET.get('id'))
        return Response(status=status.HTTP_200_OK, data=SlotService().free_slots(duration, weekdays, pk))
