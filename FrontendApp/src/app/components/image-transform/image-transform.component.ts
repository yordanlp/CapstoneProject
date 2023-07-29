import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable, Subscription, forkJoin, map } from 'rxjs';
import { io } from 'socket.io-client';
import { LatentEditsPopUpComponent } from 'src/app/components/latent-edits-pop-up/latent-edits-pop-up.component';
import { Image } from 'src/app/models/image.model';
import { LatentEdit } from 'src/app/models/latent-edit.model';
import { AppConfig } from 'src/app/services/app-config.service';
import { ImageService } from 'src/app/services/image.service';
import { UserService } from 'src/app/services/user.service';
import { v4 as uuidv4 } from 'uuid';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-image-transform',
  templateUrl: './image-transform.component.html',
  styleUrls: ['./image-transform.component.css']
})
export class ImageTransformComponent implements OnInit, OnDestroy {

  imageData: Image = null!;
  imageBlob$: Observable<any> = null!
  imagesUrl: string[] = [];
  imageSubscription: Subscription | null = null;
  loading: boolean = false;
  blobUrl: string = ""
  id: number = 0;
  currentImageUrl: string = "";
  menuOpen = false;
  @ViewChild('latentEditsModal') latentEditsModal!: LatentEditsPopUpComponent;
  socket = io(AppConfig.settings.apiServer.host);
  sanitizer: any;
  showLEModal: boolean = false;

  showModalEvent = new EventEmitter<void>();

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

  updateImageUrl( event: string ){
    this.currentImageUrl = event;
    console.log(event);
  }

  showLatentEditsModal() {
    this.latentEditsModal.showModal();
  }

  ngOnDestroy(): void {
    this.imageSubscription?.unsubscribe();
  }

  ngOnInit(): void {
    const idParam = Number(this.route.snapshot.paramMap.get('id'));
    if (isNaN(idParam))
      this.router.navigate(['/']);
    this.id = idParam;
    this.imageBlob$ = this.imageService.getImage(this.id);
    this.loading = true;
    this.imageSubscription = this.imageBlob$.subscribe(data => {
      this.blobUrl = URL.createObjectURL(data);
      this.imagesUrl = [this.blobUrl];
      this.currentImageUrl = this.blobUrl;
      this.loading = false;
    });
  }

  runPca( event: {
    interpolationSteps: number,
    latentEdits: Array<LatentEdit>
  } ){
    this.showLEModal = false;
    console.log(event);
    this.loading = true;
    let eventId = uuidv4();
    let userId = this.userService.getUser().id;
    const key = `${userId}:${eventId}`;
    this.socket.on(key, (data) => {
      this.socket.off(key);
      data = JSON.parse(data);
      if( !data.success ){
        console.error(data.message);
        return;
      }
      console.log("data from socket", data);

      let imageObservables = [];
      for (let i = 0; i < event.interpolationSteps; i++) {
        const observable = this.imageService.getGeneratedImage(this.id, i);
        imageObservables.push(observable);
      }
    
      let imagesUrls: string[] = [];
      forkJoin(imageObservables)
        .pipe(
          map( (image: any) => {
            return image;
          })
        )
        .subscribe(data => {
          for(let key in data){
            const file = data[key];
            const fileURL = URL.createObjectURL(file);
            imagesUrls.push(fileURL);
          }
          console.log("imagesUrl", imagesUrls);
          this.loading = false;
          this.imagesUrl = [this.blobUrl,...imagesUrls];
        });
      });
      
    this.imageService.runPCA(this.id, event, eventId).subscribe(
      data => console.log,
      error => console.error
    );
  }

  toggleMenu(open: boolean) {
    this.menuOpen = open;
  }
}


