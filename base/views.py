from django.shortcuts import render, redirect 
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task


class CustomLoginView(LoginView):
    template_name= 'base/login.html'
    fields= '__all__'
    redirect_authenticated_user= True
    
    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name='base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user=True 
    success_url=reverse_lazy('tasks')
    
    #once the user submit the registration form they will be directed towards the task
    def  form_valid(self, form):
        user= form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage,self).form_valid(form)
    
    ## preventing the user that already logged in seeing registration page 
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect ('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)
        



#This class inherit every fetures of Listview class
# this looks for the list of the task
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter tasks by the logged-in user
        tasks = Task.objects.filter(user=self.request.user)

        # Get the search input from the request
        search_input = self.request.GET.get('search-area', '').strip()

        # Apply search filter only if the search input is not empty
        if search_input:
            tasks = tasks.filter(title__icontains=search_input)
        else:
            # Redirect to the same page without query parameters if search is cleared
            search_input = ''  # Ensure search_input is an empty string

        # Add tasks and search input to the context
        context['tasks'] = tasks
        context['search_input'] = search_input
        context['count'] = tasks.filter(complete=False).count()

        return context


        

#detail of the task   
class TaskDetail(LoginRequiredMixin,DetailView):
    model =Task
    context_object_name='task'
    template_name='base/task.html'
    
class TaskCreate(LoginRequiredMixin, CreateView):
    model= Task 
    fields=['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')  # direct each user to  their task
    
    def form_valid(self, form):
        form.instance.user=self.request.user 
        return super(TaskCreate,self ).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task 
    fields= ['title' ,'description', 'complete']
    success_url= reverse_lazy('tasks') 


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task 
    context_object_name= 'task'
    success_url=reverse_lazy('tasks')
