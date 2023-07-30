import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AppConfig } from './app-config.service';
import { Image } from '../models/image.model';
import { LatentEdit } from '../models/latent-edit.model';

@Injectable({
  providedIn: 'root'
})
export class ImageService {

  constructor(private http: HttpClient) { }

  // Upload image
  uploadImage(imageFile: File, model: string): Observable<any> {
    const formData: FormData = new FormData();
    formData.append('model', model);
    formData.append('image', imageFile, imageFile.name);

    return this.http.post(`${AppConfig.settings.apiServer.host}/api/images/upload`, formData);
  }

  // Get all images for a user
  getImages(): Observable<any> {
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/list`);
  }

  // Get an image by id
  getImage(imageId: number): Observable<any> {
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/image/${imageId}`, { responseType: 'blob' });
  }

  generateRandomImages( model: string, numberOfImages: number, userId: string, eventId: string ): Observable<any>{
    const body = {
      model,
      numberOfImages,
      userId,
      eventId
    };
    return this.http.post(`${AppConfig.settings.apiServer.host}/api/images/generateRandom`, body);
  }

  getGeneratedImage(imageId: number, index: number): Observable<any> {
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/generated/${imageId}/${index}`, { responseType: 'blob' });
  }

  runPCA( imageId: number, parameters: { interpolationSteps: number, latentEdits: Array<LatentEdit> }, eventId: string ){
    let interpolationSteps = parameters.interpolationSteps;
    let latentEdits = parameters.latentEdits;
    const body = {
      imageId,
      interpolationSteps,
      latentEdits,
      eventId
    };
    return this.http.post(`${AppConfig.settings.apiServer.host}/api/images/pca`, body);
  }
}
