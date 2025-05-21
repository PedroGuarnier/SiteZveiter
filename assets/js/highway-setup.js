// highway-setup.js
import Highway from '@dogstudio/highway';
import Fade from './transitions/Fade';

// Initialize Highway
const H = new Highway.Core({
    transitions: {
        default: Fade
    }
});