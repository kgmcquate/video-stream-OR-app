import { NavigationMenu, NavigationMenuList, NavigationMenuLink } from "./navigation-menu"
import { VideoIcon } from "./icons"
import { Button } from "./button"

export function Header() {
    return (
      <header className="flex h-16 w-full items-center px-4 md:px-6 bg-black text-white">
        <a className="mr-6" href="#">
          <VideoIcon className="h-12 w-12" />
          {/* <span className="sr-only">LiveStream ML</span> */}
        </a>
        <NavigationMenu className="hidden lg:flex">
          <NavigationMenuList>
            {/* <NavigationMenuLink asChild>
              <a className="text-sm font-medium hover:underline underline-offset-4" href="#">
                Home
              </a>
            </NavigationMenuLink>
            <NavigationMenuLink asChild>
              <a className="text-sm font-medium hover:underline underline-offset-4" href="#">
                Streams
              </a>
            </NavigationMenuLink>
            <NavigationMenuLink asChild>
              <a className="text-sm font-medium hover:underline underline-offset-4" href="#">
                My List
              </a>
            </NavigationMenuLink> */}
          </NavigationMenuList>
        </NavigationMenu>
        <div className="ml-auto flex gap-2">
          {/* <Button variant="outline">Log In</Button>
          <Button>Sign Up</Button> */}
        </div>
      </header>
    )
  }
  