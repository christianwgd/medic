from bootstrap_modal_forms.utils import is_ajax
from django.contrib import messages
from django.shortcuts import redirect


class ModalDeleteMessageMixin:
    """
    Mixin which adds message to BSModalDeleteView and only calls the delete method if request
    is not ajax request. Since django 4 the use of 'delete' is deprecated and creates a warning.
    To avoid this warning, move the 'delete' logic to form_valid, which is the recommended way
    to deal with this.
    See also https://docs.djangoproject.com/en/4.0/releases/4.0/ -> Generic Views
    """

    # def form_valid(self, form):
    #     if not is_ajax(self.request.META):
    #         messages.success(self.request, self.success_message)
    #         return super().form_valid(form)
    #     self.object = self.get_object()
    #     return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        if not is_ajax(request.META):
            messages.success(request, self.success_message)
            return super().post(request, *args, **kwargs)
        else:
            self.object = self.get_object()
            return redirect(self.get_success_url())
