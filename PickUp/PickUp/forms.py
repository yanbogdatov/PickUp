from django import forms
from django.contrib.auth import get_user_model

user = get_user_model()

class ContactForm(forms.Form):
	fullname = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Your Full Name"}))
	email = forms.EmailField(widget=forms.EmailInput(attrs={"class":"form-control", "placeholder":"Your Email"}))
	content = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control',"placeholder":"Your message"}))

	def clean_email(self):
		email = self.cleaned_data.get("email")
		if not "gmail.com" in email:
			raise forms.ValidationError("Email should be in gmail domain")
		return email







class LoginForm(forms.Form):
	username=forms.CharField()
	password=forms.CharField(widget=forms.PasswordInput)

class RegisterForm(forms.Form):
	username=forms.CharField()
	email=forms.EmailField()
	password=forms.CharField(widget=forms.PasswordInput)
	password2=forms.CharField(label='Confirm password' ,widget=forms.PasswordInput)
	def clean_username(self):
		username=self.cleaned_data.get('username')
		qs = user.objects.filter(username = username)
		if qs.exists():
			raise forms.ValidationError("User already exists")
		return username

	def clean_email(self):
		email=self.cleaned_data.get('email')
		qs = user.objects.filter(email = email)
		if qs.exists():
			raise forms.ValidationError("Email already exists")
		return email

	def clean(self):
		data = self.cleaned_data
		password = self.cleaned_data.get('password')
		password2 = self.cleaned_data.get('password2')
		if password2 != password:
			raise forms.ValidationError("Passwords should match")
		return data
