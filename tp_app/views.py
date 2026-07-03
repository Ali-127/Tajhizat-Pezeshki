from django.shortcuts import render

def landing_view(request):
  return render(request=request, template_name='landing.html')

def shop_view(request):
  return render(request=request, template_name='shop.html')

def abount_view(request):
  return render(request=request, template_name='darabarema.html')

# def t_view(request):
#   return render(request=request, template_name='shop.html')
# def shop_view(request):
#   return render(request=request, template_name='shop.html')