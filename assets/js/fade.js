// Fade.js
import Highway from '@dogstudio/highway';
import { gsap } from 'gsap';

class Fade extends Highway.Transition {
    in({ from, to, done }) {
        // Remove old view
        from.remove();

        // Animate new view in
        gsap.fromTo(to, { opacity: 0 }, {
            opacity: 1,
            duration: 0.5,
            onComplete: done
        });
    }

    out({ from, done }) {
        // Animate old view out
        gsap.fromTo(from, { opacity: 1 }, {
            opacity: 0,
            duration: 0.5,
            onComplete: done
        });
    }
}

export default Fade;
