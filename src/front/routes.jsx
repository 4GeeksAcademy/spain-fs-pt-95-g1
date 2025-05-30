import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
} from "react-router-dom";
import { Layout } from "../front/pages/Layout";
import Home from "../front/pages/Home";
import Userview from "../front/pages/UserView";
import Categories from "../front/pages/Categories";
import AnimeCard from "./components/AnimeCard";
import Animatch from "./components/Animatch";

export const router = createBrowserRouter(
  createRoutesFromElements(
    // CreateRoutesFromElements function allows you to build route elements declaratively.
    // Create your routes here, if you want to keep the Navbar and Footer in all views, add your new routes inside the containing Route.
    // Root, on the contrary, create a sister Route, if you have doubts, try it!
    // Note: keep in mind that errorElement will be the default page when you don't get a route, customize that page to make your project more attractive.
    // Note: The child paths of the Layout element replace the Outlet component with the elements contained in the "element" attribute of these child paths.

    // Root Route: All navigation will start from here.
    <>
      {/* Ruta principal / */}
      <Route path="/" element={<Layout />} errorElement={<h1>Not found!</h1>} >
      <Route path="/" element={<Home />} />

      {/* Ruta independiente /animatch */}
      <Route path="*" element={<h1>Not found!</h1>} />
      <Route path="/anime/:id" element={<AnimeCard />} />
      <Route path="/userview" element={<Userview />} />
      <Route path="/animatch" element={<Animatch />} />
      <Route path="/categories" element={<Categories />} />
    </Route>
  </>
  )
);