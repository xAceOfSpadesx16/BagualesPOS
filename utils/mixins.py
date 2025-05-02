
class PatchMethodMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'patch':
            return self.patch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        pass