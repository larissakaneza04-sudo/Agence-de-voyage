from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import Gare, Ville
from ..forms import GareForm

class GareListView(LoginRequiredMixin, ListView):
    model = Gare
    template_name = 'reservations/gares/gare_list.html'
    context_object_name = 'gares'
    paginate_by = 10

    def get_queryset(self):
        queryset = Gare.objects.select_related('ville').order_by('ville__nom', 'nom')
        return queryset

class GareCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Gare
    form_class = GareForm
    template_name = 'reservations/gares/gare_form.html'
    success_url = reverse_lazy('gare-list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class GareUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Gare
    form_class = GareForm
    template_name = 'reservations/gares/gare_form.html'
    success_url = reverse_lazy('gare-list')

    def test_func(self):
        return self.request.user.is_staff

class GareDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Gare
    template_name = 'reservations/gares/gare_confirm_delete.html'
    success_url = reverse_lazy('gare-list')

    def test_func(self):
        return self.request.user.is_staff

def gare_detail(request, pk):
    gare = get_object_or_404(Gare.objects.select_related('ville'), pk=pk)
    context = {
        'gare': gare,
        'departs': gare.departs.all(),
        'arrivees': gare.arrivees.all()
    }
    return render(request, 'reservations/gares/gare_detail.html', context)
