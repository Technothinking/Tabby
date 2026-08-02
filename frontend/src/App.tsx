import { Route, Switch } from "wouter";
import { RunList } from "./pages/RunList";
import { RunViewer } from "./pages/RunViewer";
import "./index.css";

function App() {
  return (
    <Switch>
      <Route path="/" component={RunList} />
      <Route path="/runs/:id" component={RunViewer} />
      <Route>404: Not Found</Route>
    </Switch>
  );
}

export default App;
