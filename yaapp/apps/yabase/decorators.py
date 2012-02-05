from yabase.models import Radio

def unlock_radio_on_exception(fn):
    """ Unlock radio on request exception """
    def _dec(view_func):
        def _unlock(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except:
                radio_id = kwargs['radio_id']
                try:
                    radio = Radio.objects.get(uuid=radio_id)
                    radio.unlock()
                except Radio.DoesNotExist:
                    pass
                raise
        _unlock.__doc__ = view_func.__doc__
        _unlock.__dict__ = view_func.__dict__
        return _unlock
    return _dec(fn)