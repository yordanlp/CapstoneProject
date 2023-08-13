import { AfterViewInit, Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Carousel } from "flowbite";
import type { CarouselItem, CarouselOptions, CarouselInterface, IndicatorItem } from "flowbite";

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css']
})
export class CarouselComponent implements OnInit, AfterViewInit{
  
  private _imagesUrls: string[] = [
  ];
  @Input() 
  set imagesUrls(value: string[]) {
    this._imagesUrls = value;
    console.log(value);
    this.ngAfterViewInit();
  }

  @Output() onImageChange: EventEmitter<string> = new EventEmitter();

  get imagesUrls(): string[] {
    return this._imagesUrls;
  }

  carousel: CarouselInterface | null = null;

  initializeCarousel(){
    console.log("carousel initialized");
    let carouselItems: CarouselItem[] = this.imagesUrls.map( (u, index: number) => {
      return {
        position: index,
        el: document.getElementById(`carousel-item-${index}`)!
      };
    });

    let indicatorItems: IndicatorItem[] = this.imagesUrls.map( (u, index: number) => {
      return {
        position: index,
        el: document.getElementById(`carousel-indicator-${index}`)!
      };
    });

    let options : CarouselOptions = {
      defaultPosition: 0,
      interval: 3000,
      indicators: {
          activeClasses: 'bg-white dark:bg-gray-800',
          inactiveClasses: 'bg-white/50 dark:bg-gray-800/50 hover:bg-white dark:hover:bg-gray-800',
          items: indicatorItems
      },
      onNext: (carousel: CarouselInterface) => {
          console.log('next slider item is shown', carousel);
          const imageUrl = this.imagesUrls[carousel._activeItem.position];
          console.log(carousel);
          this.onImageChange.emit(imageUrl);
      },
      onPrev: (carousel: CarouselInterface) => {
          console.log('previous slider item is shown', carousel);
          const imageUrl = this.imagesUrls[carousel._activeItem.position];
          this.onImageChange.emit(imageUrl);
      },
      onChange: (carousel: CarouselInterface) => {
        const imageUrl = this.imagesUrls[carousel._activeItem.position];
          this.onImageChange.emit(imageUrl);
          console.log('new slider item has been shown', carousel);
      }
    };

    if( this.imagesUrls.length > 1 )
      this.carousel = new Carousel(carouselItems, options);
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.initializeCarousel();
    });
  }

  nextImage(){
    this.carousel?.next();
  }

  previousImage(){
    this.carousel?.prev();
  }
  ngOnInit(): void {
  
  }
}
