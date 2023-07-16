import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable, Subscription } from 'rxjs';
import { io } from 'socket.io-client';
import { LatentEditsPopUpComponent } from 'src/app/components/latent-edits-pop-up/latent-edits-pop-up.component';
import { Image } from 'src/app/models/image.model';
import { LatentEdit } from 'src/app/models/latent-edit.model';
import { AppConfig } from 'src/app/services/app-config.service';
import { ImageService } from 'src/app/services/image.service';
import { UserService } from 'src/app/services/user.service';
import { v4 as uuidv4 } from 'uuid';

@Component({
  selector: 'app-image-transform',
  templateUrl: './image-transform.component.html',
  styleUrls: ['./image-transform.component.css']
})
export class ImageTransformComponent implements OnInit, OnDestroy {

  imageData: Image = null!;
  imageBlob$: Observable<any> = null!
  imageSubscription: Subscription | null = null;
  blobUrl: string = ""
  id: number = 0;
  menuOpen = false;
  @ViewChild('latentEditsModal') latentEditsModal!: LatentEditsPopUpComponent;
  socket = io(AppConfig.settings.apiServer.host);

  constructor(private imageService: ImageService
    , private route: ActivatedRoute
    , private router: Router
    , private userService: UserService )
    {

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
    this.imageSubscription = this.imageBlob$.subscribe(data => {
      this.blobUrl = URL.createObjectURL(data);
    });
  }

  runPca( event: Array<LatentEdit> ){
    console.log(event);
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
      this.imageBlob$ = this.imageService.getGeneratedImage(this.id);
      this.imageSubscription = this.imageBlob$.subscribe(data => {
      this.blobUrl = URL.createObjectURL(data);
    });
      console.log(data);
      
    });
    this.imageService.runPCA(this.id, event, eventId).subscribe(
      data => console.log,
      error => console.error
    );
  }

  showLatentEditsModal(){
    this.latentEditsModal.showModal();
  }

  toggleMenu(open: boolean) {
    this.menuOpen = open;
  }
}
