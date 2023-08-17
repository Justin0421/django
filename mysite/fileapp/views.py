from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from .forms import FileUploadForm
import os
from django.conf import settings

from .read_level import handle_uploaded_file
from .file_serach import get_files_without_numbers

# 多文件上传
from django.views.generic.edit import FormView
from .forms import FileFieldForm


#子应用主页
def fileapp_home(request):
    return render(request, 'fileapp/fileapp_home.html')

# 单文件上传
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            handle_uploaded_file(file)
            # file = form.cleaned_data['file']
            # file_path = './data_file/' +  "test.txt"
            # file_write = open(file_path,'w')
            # 处理文件保存等操作
            return render(request, 'fileapp/upload.html', {'form': form})
    else:
        form = FileUploadForm()
    return render(request, 'fileapp/upload.html', {'form': form})


def upload_success(request):
    # """ 上传成功响应 """
    return HttpResponse('多文件上传成功！')



# 文件下载页面
def download_page(request):
    # folder_path = os.path.join(settings.MEDIA_ROOT, 'files')  # 文件夹路径，这里假设你的文件存储在 MEDIA_ROOT/files 目录下
    # print(folder_path)
    # file_list = os.listdir(folder_path)  # 获取文件列表
    folder_path = 'mysite/fileapp/file_data/outcome_alldata'  # 替换为你的文件夹路径
    file_list = get_files_without_numbers(folder_path)
    context = {
        'file_list': file_list,
    }
    return render(request, 'fileapp/download_page.html', context)

# 下载文件
def download_file(request,filename):
    # 处理文件下载操作
    folder_path = 'mysite/fileapp/file_data/outcome_alldata'  # 替换为你的文件夹路径
    file_path = os.path.join(folder_path, filename)  # 文件路径
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        raise Http404("File does not exist.")
    
    
    # with open(file_path, 'rb') as f:
    #     response = HttpResponse(f.read(), content_type='application/octet-stream')
    #     response['Content-Disposition'] = 'attachment; filename="' + os.path.basename(file_path) + '"'
    #     return response

# 多文件上传    
class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = "fileapp/upload.html"  # Replace with your template.
    # success_url = "..."  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        for f in files:
           handle_uploaded_file(f)  # Do something with each file.
        # return super().form_valid()
        return HttpResponse('多文件上传成功！')