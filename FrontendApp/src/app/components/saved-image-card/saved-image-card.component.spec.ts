import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SavedImageCardComponent } from './saved-image-card.component';

describe('SavedImageCardComponent', () => {
  let component: SavedImageCardComponent;
  let fixture: ComponentFixture<SavedImageCardComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SavedImageCardComponent]
    });
    fixture = TestBed.createComponent(SavedImageCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
