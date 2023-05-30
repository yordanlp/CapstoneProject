import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppConfig } from 'src/app/services/app-config.service';
import { UserService } from 'src/app/services/user.service';
@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {

  registerForm: FormGroup;
  formSubmitted = false;

  constructor(private formBuilder: FormBuilder, private userService: UserService) {

    let apiServer = AppConfig.settings.apiServer;

    this.registerForm = this.formBuilder.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    this.registerForm = this.formBuilder.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit(): void {
    this.formSubmitted = true;

    if (this.registerForm.invalid) {
      return;
    }

    const username = this.registerForm.value.username;
    const email = this.registerForm.value.email;
    const password = this.registerForm.value.password;

    this.userService.registerUser(username, email, password).subscribe(
      response => {
        // Handle success response
        console.log('User registered successfully:', response);
      },
      error => {
        // Handle error response
        console.error('Failed to register user:', error);
      }
    );
  }
}
