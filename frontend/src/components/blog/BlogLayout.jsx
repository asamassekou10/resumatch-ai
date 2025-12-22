import { Outlet } from 'react-router-dom';
import Footer from '../ui/Footer';

/**
 * Blog Layout Component
 * 
 * Provides consistent layout for blog pages
 */
const BlogLayout = () => {
  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Background atmosphere */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black z-0 pointer-events-none" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 z-0 pointer-events-none" />
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="relative z-10">
        <Outlet />
      </div>
      <Footer />
    </div>
  );
};

export default BlogLayout;


