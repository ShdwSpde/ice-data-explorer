// vr/js/components/narrative-placard.js
AFRAME.registerComponent('narrative-placard', {
  schema: {
    type:    { type: 'string',  default: 'watchdog' },
    speaker: { type: 'string',  default: '' },
    date:    { type: 'string',  default: '' },
    body:    { type: 'string',  default: '' },
    source:  { type: 'string',  default: '' },
    width:   { type: 'number',  default: 2.2 },
    height:  { type: 'number',  default: 1.5 }
  },

  init: function () {
    // placeholder — renders nothing yet
    console.log('[narrative-placard] init', this.data.type);
  }
});
