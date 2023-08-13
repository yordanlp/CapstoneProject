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

  saveImage(imageFile: File, parentImageId: number){
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('parentImageId', parentImageId.toString());
    return this.http.post(`${AppConfig.settings.apiServer.host}/api/images/save`, formData);
  }
  // Get all images for a user
  getImages(): Observable<any> {
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/list`);
  }

  getSavedImages(): Observable<any>{
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/saved/list`);
  }

  // Get an image by id
  getImage(imageId: number): Observable<any> {
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/image/${imageId}`, { responseType: 'blob' });
  }

  // Detele an image given id
  deleteImage(imageId: number): Observable<any> {
    console.log(`IMAGE ID FOR REMOVE ${imageId}`);
    return this.http.delete(`${AppConfig.settings.apiServer.host}/api/images/image/${imageId}`);
  }

  getSavedImage(imageId: number): Observable<any> {
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/saved/image/${imageId}`, { responseType: 'blob' });
  }

  getSuperResolutionImage(imageId: number): Observable<any>{
    return this.http.get(`${AppConfig.settings.apiServer.host}/api/images/superresolution/image/${imageId}`, { responseType: 'blob' });
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

  runSuperResolution( imageId: number, eventId: string ){
    const body = {
      imageId,
      eventId
    };
    return this.http.post(`${AppConfig.settings.apiServer.host}/api/images/superresolution`, body);
  }
  
}
