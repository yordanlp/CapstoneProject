import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LatentEditsPopUpComponent } from './latent-edits-pop-up.component';

describe('LatentEditsPopUpComponent', () => {
  let component: LatentEditsPopUpComponent;
  let fixture: ComponentFixture<LatentEditsPopUpComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [LatentEditsPopUpComponent]
    });
    fixture = TestBed.createComponent(LatentEditsPopUpComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
