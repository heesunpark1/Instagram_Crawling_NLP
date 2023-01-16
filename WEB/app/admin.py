from django.contrib.admin import AdminSite

from .models import *
from .forms import SentAnalyzerForm
from django.template.response import TemplateResponse

class MyAdminSite(AdminSite):
    site_header = 'Instagram Sentimental Analyzer'
    index_title = '당신의 인스타그램 피드글을 입력하세요.'
    index_template = 'main.html'

    def index(self, request):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = self.get_app_list(request)

        # INITIAL_DATA = {'text': '내 감성은 무엇이냐'}

        form = SentAnalyzerForm(
            # initial=INITIAL_DATA
        )
        #         return render(request, 'index.html', {'form': form})

        context = dict(
            self.each_context(request),
            title=self.index_title,
            app_list=app_list,
        )
        context.update({'form': form})

        request.current_app = self.name

        return TemplateResponse(request, self.index_template, context)


admin_site = MyAdminSite(name='myadmin')
admin_site.register(SentAnalyzer)
admin_site.register(Instagram)