import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AppConfig } from './app-config.service';

@Injectable({
  providedIn: 'root'
})
export class ImageService {

  constructor(private http: HttpClient) { }

  // Upload image
  uploadImage(imageFile: File): Observable<any> {
    const formData: FormData = new FormData();
    formData.append('image', imageFile, imageFile.name);

    return this.http.post(`${AppConfig.settings.apiServer.host}/api/images/upload`, formData);
  }

  // Get all images for a user
  getImages(): Observable<any> {
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/list`);
  }

  // Get an image by id
  getImage(imageId: string): Observable<any> {
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/image/${imageId}`, { responseType: 'blob' });
  }
}
