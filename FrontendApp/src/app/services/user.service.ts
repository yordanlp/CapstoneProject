import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppConfig } from './app-config.service';
import { Observable } from 'rxjs';

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

  login(email: string, password: string): Observable<any> {
    return this.http.post<any>(`${AppConfig.settings.apiServer.host}/api/users/login`, { email, password });
  }
}

