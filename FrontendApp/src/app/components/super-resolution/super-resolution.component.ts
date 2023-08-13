import { HttpClient } from '@angular/common/http';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable, Subscription, map } from 'rxjs';
import { io } from 'socket.io-client';
import { SavedImage } from 'src/app/models/saved-image.model';
import { AppConfig } from 'src/app/services/app-config.service';
import { ImageService } from 'src/app/services/image.service';
import { UserService } from 'src/app/services/user.service';
import { v4 as uuidv4 } from 'uuid';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-super-resolution',
  templateUrl: './super-resolution.component.html',
  styleUrls: ['./super-resolution.component.css']
})
export class SuperResolutionComponent implements OnInit, OnDestroy{
  imageData: SavedImage = null!;
  imageBlob$: Observable<any> = null!
  imagesUrl: string[] = [];
  imageSubscription: Subscription | null = null;
  superResolutionSubscription: Subscription | null = null;
  loading: boolean = false;
  blobUrl: string = ""
  id: number = 0;
  currentImageUrl: string = "";
  socket = io(AppConfig.settings.apiServer.host);
  sanitizer: any;
  menuOpen: boolean = false;

  constructor(private imageService: ImageService
    , private route: ActivatedRoute
    , private router: Router
    , private userService: UserService
    , private http: HttpClient )
    {

  }

  downloadImage(){
    this.http.get(this.currentImageUrl, { responseType: 'blob' }).subscribe(blob => {
      let name = uuidv4();
      saveAs(blob, name + ".jpg");
    });
  }

  convertBlobUrlToFile(blobUrl: string): Observable<File> {
    return this.http.get(blobUrl, { responseType: 'blob' }).pipe(
      map(blob => new File([blob], 'filename.png', { type: 'image/png' }))
    );
  }

  updateImageUrl( event: string ){
    this.currentImageUrl = event;
    console.log(event);
  }

  ngOnDestroy(): void {
    this.imageSubscription?.unsubscribe();
    this.superResolutionSubscription?.unsubscribe();
  }

  ngOnInit(): void {
    const idParam = Number(this.route.snapshot.paramMap.get('id'));
    if (isNaN(idParam))
      this.router.navigate(['/']);
    this.id = idParam;
    this.imageBlob$ = this.imageService.getSavedImage(this.id);
    this.loading = true;
    this.imageSubscription = this.imageBlob$.subscribe(data => {
      this.blobUrl = URL.createObjectURL(data);
      this.imagesUrl = [this.blobUrl];
      this.currentImageUrl = this.blobUrl;
      this.loading = false;
      this.loadSuperResolution();
    });
  }

  loadSuperResolution(){
    this.loading = true;
    this.superResolutionSubscription = this.imageService.getSuperResolutionImage(this.id).subscribe(
      data => {
        const superResolutionUrl = URL.createObjectURL(data);
        this.imagesUrl = [...this.imagesUrl, superResolutionUrl];
        this.loading = false;
      },
      error => {
        this.loading = false;
        if (error.status === 404) {
          console.error('Resource not found:', error);
        } else {
          console.error('An error occurred:', error);
        }
      });
  }

  runSuperResolution(){
    this.loading = true;
    let eventId = uuidv4();
    let userId = this.userService.getUser().id;
    const key = `${userId}:${eventId}`;
    this.loading = true;
    this.socket.on(key, (data) => {
      this.socket.off(key);
      data = JSON.parse(data);
      this.loading = false;
      if( !data.success ){
        console.error(data.message);
        return;
      }
      this.loadSuperResolution();
      console.log("data from socket", data);    
    });
      
    this.imageService.runSuperResolution(this.id, eventId).subscribe(
      data => console.log,
      error => console.error
    );
  }

  toggleMenu(open: boolean) {
    this.menuOpen = open;
  }
}
