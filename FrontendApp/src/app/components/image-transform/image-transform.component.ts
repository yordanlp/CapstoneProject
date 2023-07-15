import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable, Subscription } from 'rxjs';
import { LatentEditsPopUpComponent } from 'src/app/latent-edits-pop-up/latent-edits-pop-up.component';
import { Image } from 'src/app/models/image.model';
import { LatentEdit } from 'src/app/models/latent-edit.model';
import { ImageService } from 'src/app/services/image.service';

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

  constructor(private imageService: ImageService
    , private route: ActivatedRoute
    , private router: Router) {

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

  showLatentEditsModal(){
    this.latentEditsModal.showModal();
  }

  toggleMenu(open: boolean) {
    this.menuOpen = open;
  }
}
