import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppConfig } from './app-config.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient) { }

  registerUser(username: string, email: string, password: string) {
    const body = {
      username: username,
      email: email,
      password: password
    };
    return this.http.post(`${AppConfig.settings.apiServer.host}/api/users/register`, body);
  }
}
