import { Sidebar } from '@/components/sidebar'
import Login from '@/pages/login'
import {BrowserRouter, Route, Routes} from 'react-router-dom'
import Home from './page'
import Categories from '@/pages/categories'


function App(){
    return(
        <BrowserRouter>
            <Routes>
                <Route path='/' element={<Login/>}/>
                <Route path='/Home' element={<Sidebar/>}/>
                <Route path='/categories' element={<Categories/>}/>
            </Routes>
        </BrowserRouter>
    )
}

export default App