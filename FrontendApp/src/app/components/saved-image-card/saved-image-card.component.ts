import { Component, Input } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { SavedImage } from 'src/app/models/saved-image.model';
import { ImageService } from 'src/app/services/image.service';

@Component({
  selector: 'app-saved-image-card',
  templateUrl: './saved-image-card.component.html',
  styleUrls: ['./saved-image-card.component.css']
})
export class SavedImageCardComponent {
  @Input() imageData: SavedImage = null!;
  imageBlob$: Observable<any> = null!
  imageSubscription: Subscription = null!;
  blobUrl: string = ""

  constructor(private imageService: ImageService) {

  }
  ngOnInit(): void {
    this.imageBlob$ = this.imageService.getSavedImage(this.imageData.id);
    this.imageSubscription = this.imageBlob$.subscribe(data => {
      this.blobUrl = URL.createObjectURL(data);
      console.log(this.blobUrl);
    });
  }
}
